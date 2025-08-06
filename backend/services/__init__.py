#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package des services pour Le Mixologue Augmenté

Contient les services métier de l'application :
- MistralService : Intégration avec l'API Mistral pour la génération de cocktails

Auteur: Assistant IA
Date: 2024
"""

from .mistral_service import MistralService

__all__ = ['MistralService']