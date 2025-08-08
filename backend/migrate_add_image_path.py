#!/usr/bin/env python3
"""
Script de migration pour ajouter la colonne image_path à la table cocktails.

Ce script ajoute la nouvelle colonne image_path à la base de données existante
pour stocker les chemins des images générées et éviter la régénération.
"""

import os
import sqlite3
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def migrate_database():
    """
    Ajoute la colonne image_path à la table cocktails si elle n'existe pas.
    """
    # Récupérer l'URL de la base de données
    database_url = os.getenv('DATABASE_URL', 'sqlite:///cocktails.db')
    
    # Extraire le chemin du fichier SQLite
    if database_url.startswith('sqlite:///'):
        db_filename = database_url.replace('sqlite:///', '')
        # La base de données Flask est créée dans le répertoire instance
        db_path = os.path.join('instance', db_filename)
    else:
        print("❌ Cette migration ne supporte que SQLite")
        return False
    
    # Vérifier si le fichier de base de données existe
    if not os.path.exists(db_path):
        print(f"❌ Fichier de base de données non trouvé: {db_path}")
        return False
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier si la colonne existe déjà
        cursor.execute("PRAGMA table_info(cocktails)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'image_path' in columns:
            print("✅ La colonne image_path existe déjà")
            conn.close()
            return True
        
        # Ajouter la nouvelle colonne
        print("📝 Ajout de la colonne image_path...")
        cursor.execute("""
            ALTER TABLE cocktails 
            ADD COLUMN image_path VARCHAR(500)
        """)
        
        # Valider les changements
        conn.commit()
        
        # Vérifier que la colonne a été ajoutée
        cursor.execute("PRAGMA table_info(cocktails)")
        columns_after = [column[1] for column in cursor.fetchall()]
        
        if 'image_path' in columns_after:
            print("✅ Colonne image_path ajoutée avec succès")
            
            # Afficher le nombre de cocktails existants
            cursor.execute("SELECT COUNT(*) FROM cocktails")
            count = cursor.fetchone()[0]
            print(f"📊 {count} cocktails existants pourront bénéficier de la mise en cache d'images")
            
            conn.close()
            return True
        else:
            print("❌ Erreur: La colonne n'a pas été ajoutée")
            conn.close()
            return False
            
    except sqlite3.Error as e:
        print(f"❌ Erreur SQLite: {e}")
        if 'conn' in locals():
            conn.close()
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def verify_migration():
    """
    Vérifie que la migration s'est bien déroulée.
    """
    database_url = os.getenv('DATABASE_URL', 'sqlite:///cocktails.db')
    db_filename = database_url.replace('sqlite:///', '')
    # La base de données Flask est créée dans le répertoire instance
    db_path = os.path.join('instance', db_filename)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier la structure de la table
        cursor.execute("PRAGMA table_info(cocktails)")
        columns = cursor.fetchall()
        
        print("\n📋 Structure actuelle de la table cocktails:")
        for column in columns:
            col_id, name, col_type, not_null, default, pk = column
            print(f"  - {name}: {col_type}{'*' if not_null else ''} {'(PK)' if pk else ''}")
        
        # Vérifier s'il y a des données
        cursor.execute("SELECT COUNT(*) FROM cocktails")
        count = cursor.fetchone()[0]
        print(f"\n📊 Nombre total de cocktails: {count}")
        
        if count > 0:
            cursor.execute("SELECT COUNT(*) FROM cocktails WHERE image_path IS NOT NULL")
            with_images = cursor.fetchone()[0]
            print(f"📸 Cocktails avec image générée: {with_images}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

if __name__ == '__main__':
    print("🔄 Migration: Ajout de la colonne image_path\n")
    
    # Exécuter la migration
    success = migrate_database()
    
    if success:
        print("\n🔍 Vérification de la migration...")
        verify_migration()
        print("\n✨ Migration terminée avec succès!")
        print("\n💡 Les images générées seront maintenant mises en cache pour éviter la régénération.")
    else:
        print("\n❌ La migration a échoué")
        exit(1)