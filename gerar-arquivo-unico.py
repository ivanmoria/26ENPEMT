#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gera index-completo.html: uma cópia do site com todas as imagens embutidas
e sem comentários HTML.

Serve para entregar o site como ARQUIVO ÚNICO — quem publica não precisa
receber a pasta img/ nem se preocupar em manter a estrutura de diretórios.

Use quando quiser entregar um arquivo só.

Para o site normal, continue usando index.html + pasta img/,
que carrega mais rápido (o navegador guarda cada imagem em cache separadamente).

    python3 gerar-arquivo-unico.py
"""

import base64
import io
import mimetypes
import os
import re
import sys

ORIGEM = 'index.html'
DESTINO = 'XXVIENPEMT.html'


def main():

    if not os.path.exists(ORIGEM):
        sys.exit('não encontrei ' + ORIGEM)

    s = io.open(ORIGEM, encoding='utf-8').read()

    # Remove todos os comentários HTML, inclusive comentários
    # que ocupam várias linhas.
    s = re.sub(r'<!--.*?-->', '', s, flags=re.DOTALL)

    caminhos = sorted(set(
        re.findall(r'(?:src|href)="(img/[^"]+)"', s) +
        re.findall(r"url\(['\"]?(img/[^'\")]+)", s)
    ))

    total = 0
    faltando = []

    for c in caminhos:

        if not os.path.exists(c):
            faltando.append(c)
            continue

        tipo = mimetypes.guess_type(c)[0] or 'application/octet-stream'

        dados = base64.b64encode(
            io.open(c, 'rb').read()
        ).decode('ascii')

        uri = 'data:%s;base64,%s' % (tipo, dados)

        # src / href
        s = s.replace('"' + c + '"', '"' + uri + '"')

        # url('...')
        s = s.replace("'" + c + "'", "'" + uri + "'")

        total += os.path.getsize(c)

        print(
            '  embutida  %-38s %7.0f KB'
            % (c, os.path.getsize(c) / 1024)
        )

    if faltando:

        print('\n  AVISO — não encontradas, ficaram como link:')

        for f in faltando:
            print('   ', f)

    io.open(DESTINO, 'w', encoding='utf-8').write(s)

    sobrou = re.findall(
        r'(?:src|href)="(img/[^"]+)"',
        s
    )

    print(
        '\n  %s: %.2f MB  (%d imagens, %.2f MB de origem)'
        % (
            DESTINO,
            os.path.getsize(DESTINO) / 1024 / 1024,
            len(caminhos),
            total / 1024 / 1024
        )
    )

    print(
        '  referências a img/ restantes:',
        len(sobrou) or 'nenhuma'
    )


main()