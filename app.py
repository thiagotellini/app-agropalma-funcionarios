from flask import Flask, render_template, request
import pyodbc
import base64
import os
from config import DB_CONFIG


app = Flask(__name__)

# Configurações de conexão com o SQL Server
conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={DB_CONFIG['server']};"
    f"DATABASE={DB_CONFIG['database']};"
    f"UID={DB_CONFIG['username']};"
    f"PWD={DB_CONFIG['password']}"
)

@app.route('/Aniversariantes')
def index():
    query = """ 
        WITH CTE AS (
            SELECT 
                f.nomfun AS [Nome Funcionario],
                o.nomloc AS [Departamento],
                c.titcar AS [Cargo],
                f.datadm AS [Data de Admissao],
                f.numemp AS [Num Emp R034FUN],
                fot.numemp AS [Num Emp FOT],
                f.numcad AS [Num Cad R034FUN],
                fot.numcad AS [NUm Cad FOT],
                f.tipcol AS [TIPO FUN R034FUN],
                fot.tipcol AS [TIPO FUN FOT],
                (CASE 
                    WHEN f.numemp = 4 AND f.codfil = 1 THEN 'Belém'
                    WHEN f.numemp = 600 AND f.codfil = 4 THEN 'Limeira'
                    WHEN f.numemp = 4 AND f.codfil = 4 THEN 'São Paulo'
                    WHEN f.numemp = 2 AND f.codfil = 1 THEN 'Tailandia'
                    WHEN f.numemp = 2 AND f.codfil = 4 THEN 'Tailandia'
                    WHEN f.numemp = 2 AND f.codfil = 7 THEN 'Tailandia'
                    WHEN f.numemp = 2 AND f.codfil = 6 THEN 'Tailandia'
                    ELSE e.apeemp  -- Mantém o original se não estiver no mapeamento
                END) AS [Empresa],
                f.datnas AS [Data Nascimento],
                (CASE 
                    WHEN f.sitafa = 2 THEN (SELECT MAX(iniafa) 
                                            FROM r040feg 
                                            WHERE numemp = f.numemp 
                                            AND tipcol = f.tipcol 
                                            AND numcad = f.numcad) 
                    ELSE NULL 
                END) AS DtInicioFeriasColab,
                (CASE 
                    WHEN f.sitafa = 2 THEN (SELECT MAX(terafa) 
                                            FROM r040feg 
                                            WHERE numemp = f.numemp 
                                            AND tipcol = f.tipcol 
                                            AND numcad = f.numcad) 
                    ELSE NULL 
                END) AS DtFimFeriasColab,
                DATEDIFF(DAY, 
                    (CASE 
                        WHEN f.sitafa = 2 THEN (SELECT MAX(iniafa) 
                                                FROM r040feg 
                                                WHERE numemp = f.numemp 
                                                AND tipcol = f.tipcol 
                                                AND numcad = f.numcad) 
                        ELSE NULL 
                    END), 
                    (CASE 
                        WHEN f.sitafa = 2 THEN (SELECT MAX(terafa) 
                                                FROM r040feg 
                                                WHERE numemp = f.numemp 
                                                AND tipcol = f.tipcol 
                                                AND numcad = f.numcad) 
                        ELSE NULL 
                    END)) AS QtdDiasFerias,
                DATEDIFF(DAY, GETDATE(), DATEADD(YEAR, YEAR(GETDATE()) - YEAR(f.datnas) + 
                    CASE WHEN MONTH(GETDATE()) > MONTH(f.datnas) OR 
                          (MONTH(GETDATE()) = MONTH(f.datnas) AND DAY(GETDATE()) > DAY(f.datnas)) 
                         THEN 1 ELSE 0 END, f.datnas)) AS QtdDiasAniversario,
                'PARABÉNS POR SEU DIA' AS Mensagem,
                ROW_NUMBER() OVER (PARTITION BY f.nomfun ORDER BY f.datadm DESC) AS rn,
                fot.fotemp -- Coluna de foto
            FROM 
                r034fun AS f
            JOIN 
                r030emp AS e ON f.numemp = e.numemp
            JOIN 
                r024car AS c ON f.codcar = c.codcar
            JOIN 
                r016orn AS o ON f.taborg = o.taborg AND f.numloc = o.numloc
            JOIN 
                r010sit AS s ON f.sitafa = s.codsit
            INNER JOIN 
                r034FOT AS fot ON f.numcad = fot.numcad
                AND f.numemp = fot.numemp
                AND f.tipcol = fot.tipcol
            WHERE 
                f.sitafa = 1
                AND MONTH(f.datnas) = MONTH(GETDATE())  
                AND DAY(f.datnas) >= DAY(GETDATE())    
        )
        SELECT 
            [Nome Funcionario],
            [Departamento],
            [Empresa],
            [Data Nascimento],
            (CASE 
                WHEN QtdDiasAniversario = 0 THEN 'Hoje' 
                ELSE CONVERT(VARCHAR, QtdDiasAniversario) 
            END) AS QtdDiasAniversario,
            (CASE 
                WHEN QtdDiasAniversario = 0 THEN 'Parabéns por seu dia' 
                ELSE '' 
            END) AS Mensagem,
            fotemp, 
            [Num Emp R034FUN],
            [Num Emp FOT],
            [Num Cad R034FUN],
            [NUm Cad FOT]
        FROM 
            CTE
        WHERE 
            rn = 1
        ORDER BY 
            (CASE WHEN QtdDiasAniversario = 0 THEN 0 ELSE 1 END), 
            [Nome Funcionario]
    """
    
    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in data]
        
        for result in results:
            if result['fotemp']:
                result['fotemp'] = 'data:image/jpeg;base64,' + base64.b64encode(result['fotemp']).decode('utf-8')

    return render_template('Aniversariantes.html', results=results)

@app.route('/Ferias')
def index_Ferias():
    query = """ 
        WITH CTE AS (
            SELECT 
                f.nomfun AS [Nome Funcionario],
                o.nomloc AS [Departamento],
                c.titcar AS [Cargo],
                f.datadm AS [Data de Admissao],
                (CASE 
                    WHEN f.numemp = 4 AND f.codfil = 1 THEN 'Belém'
                    WHEN f.numemp = 600 AND f.codfil = 4 THEN 'Limeira'
                    WHEN f.numemp = 4 AND f.codfil = 4 THEN 'São Paulo'
                    WHEN f.numemp = 2 AND f.codfil = 1 THEN 'Tailandia'
                    WHEN f.numemp = 2 AND f.codfil = 4 THEN 'Tailandia'
                    WHEN f.numemp = 2 AND f.codfil = 7 THEN 'Tailandia'
                    ELSE e.apeemp  -- Mantém o original se não estiver no mapeamento
                END) AS [Empresa],
                (CASE 
                    WHEN f.sitafa = 1 THEN (SELECT MAX(iniafa) 
                                            FROM r040feg 
                                            WHERE numemp = f.numemp 
                                            AND tipcol = f.tipcol 
                                            AND numcad = f.numcad) 
                    ELSE NULL 
                END) AS InicioFerias,
                (CASE 
                    WHEN f.sitafa = 1 THEN (SELECT MAX(terafa) 
                                            FROM r040feg 
                                            WHERE numemp = f.numemp 
                                            AND tipcol = f.tipcol 
                                            AND numcad = f.numcad) 
                    ELSE NULL 
                END) AS FimFerias,
                DATEDIFF(DAY, 
                    (CASE 
                        WHEN f.sitafa = 1 THEN (SELECT MAX(iniafa) 
                                                FROM r040feg 
                                                WHERE numemp = f.numemp 
                                                AND tipcol = f.tipcol 
                                                AND numcad = f.numcad) 
                        ELSE NULL 
                    END), 
                    (CASE 
                        WHEN f.sitafa = 1 THEN (SELECT MAX(terafa) 
                                                FROM r040feg 
                                                WHERE numemp = f.numemp 
                                                AND tipcol = f.tipcol 
                                                AND numcad = f.numcad) 
                        ELSE NULL 
                    END)) AS QtdDiasFerias,
                DATEDIFF(DAY, GETDATE(), DATEADD(YEAR, YEAR(GETDATE()) - YEAR(f.datnas) + 
                    CASE WHEN MONTH(GETDATE()) > MONTH(f.datnas) OR 
                          (MONTH(GETDATE()) = MONTH(f.datnas) AND DAY(GETDATE()) > DAY(f.datnas)) 
                    THEN 1 ELSE 0 END, f.datnas)) AS QtdDiasAniversario,
                ROW_NUMBER() OVER (PARTITION BY f.nomfun ORDER BY f.datadm DESC) AS rn,
                fot.fotemp AS Fotografia
            FROM 
                r034fun AS f
            JOIN 
                r030emp AS e ON f.numemp = e.numemp
            JOIN 
                r024car AS c ON f.codcar = c.codcar
            JOIN 
                r016orn AS o ON f.taborg = o.taborg AND f.numloc = o.numloc
            JOIN 
                r010sit AS s ON f.sitafa = s.codsit
            INNER JOIN 
                r034FOT AS fot ON f.numcad = fot.numcad
                AND f.numemp = fot.numemp
                AND f.tipcol = fot.tipcol
            WHERE 
                f.sitafa <> 7
                AND NOT EXISTS (
                    SELECT 1 
                    FROM r040feg 
                    WHERE numemp = f.numemp 
                    AND tipcol = f.tipcol 
                    AND numcad = f.numcad 
                    AND f.sitafa = 2
                )
        )
        SELECT 
            [Nome Funcionario],
            [Departamento],
            [Cargo],
            [Empresa],
            InicioFerias,
            FimFerias,
            QtdDiasFerias,
            Fotografia
        FROM 
            CTE
        WHERE 
            rn = 1
            AND (
                (InicioFerias IS NOT NULL AND InicioFerias > GETDATE())  -- Férias futuras
                OR 
                (InicioFerias IS NOT NULL AND InicioFerias <= GETDATE() AND FimFerias >= GETDATE())  -- Férias atuais
            )
        ORDER BY 
            [Nome Funcionario];

    """
    
    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in data]
        
        for result in results:
            if result['Fotografia']:
                try:
                    if isinstance(result['Fotografia'], bytes):
                        result['Fotografia'] = 'data:image/jpeg;base64,' + base64.b64encode(result['Fotografia']).decode('utf-8')
                except Exception as e:
                    print(f"Erro ao codificar a imagem: {e}")
                    result['Fotografia'] = None

    return render_template('Ferias.html', results=results)

@app.route('/Novos_Colaboradores')
def index_Novos_Colaboradores():
    query = """ 
        WITH CTE AS (
            SELECT 
                f.nomfun AS [Nome Funcionario],
                o.nomloc AS [Departamento],
                c.titcar AS [Cargo],
                f.datadm AS [Data de Admissao],
                (CASE 
                    WHEN f.numemp = 4 AND f.codfil = 1 THEN 'Belém'
                    WHEN f.numemp = 600 AND f.codfil = 4 THEN 'Limeira'
                    WHEN f.numemp = 4 AND f.codfil = 4 THEN 'São Paulo'
                    WHEN f.numemp = 2 AND f.codfil = 1 THEN 'Tailandia'
                    WHEN f.numemp = 2 AND f.codfil = 4 THEN 'Tailandia'
                    WHEN f.numemp = 2 AND f.codfil = 7 THEN 'Tailandia'
                    WHEN f.numemp = 2 AND f.codfil = 6 THEN 'Tailandia'
                    ELSE e.apeemp  -- Mantém o original se não estiver no mapeamento
                END) AS [Empresa],
                (CASE 
                    WHEN f.sitafa = 2 THEN 
                        (SELECT MAX(iniafa) 
                         FROM r040feg 
                         WHERE numemp = f.numemp 
                         AND tipcol = f.tipcol 
                         AND numcad = f.numcad) 
                    ELSE NULL 
                END) AS DtInicioFeriasColab,
                (CASE 
                    WHEN f.sitafa = 2 THEN 
                        (SELECT MAX(terafa) 
                         FROM r040feg 
                         WHERE numemp = f.numemp 
                         AND tipcol = f.tipcol 
                         AND numcad = f.numcad) 
                    ELSE NULL 
                END) AS DtFimFeriasColab,
                DATEDIFF(DAY, 
                    (CASE 
                        WHEN f.sitafa = 2 THEN
                            (SELECT MAX(iniafa) 
                             FROM r040feg 
                             WHERE numemp = f.numemp 
                             AND tipcol = f.tipcol 
                             AND numcad = f.numcad) 
                        ELSE NULL 
                    END), 
                    (CASE 
                        WHEN f.sitafa = 2 THEN
                            (SELECT MAX(terafa) 
                             FROM r040feg 
                             WHERE numemp = f.numemp 
                             AND tipcol = f.tipcol 
                             AND numcad = f.numcad) 
                        ELSE NULL 
                    END)) AS QtdDiasFerias,
                DATEDIFF(DAY, GETDATE(), DATEADD(YEAR, YEAR(GETDATE()) - YEAR(f.datnas) + 
                    CASE WHEN MONTH(GETDATE()) > MONTH(f.datnas) OR 
                          (MONTH(GETDATE()) = MONTH(f.datnas) AND DAY(GETDATE()) > DAY(f.datnas)) 
                     THEN 1 ELSE 0 END, f.datnas)) AS QtdDiasAniversario,
                ROW_NUMBER() OVER (PARTITION BY f.nomfun ORDER BY f.datadm DESC) AS rn,
                fot.fotemp AS Fotografia
            FROM 
                r034fun AS f
            JOIN 
                r030emp AS e ON f.numemp = e.numemp
            JOIN 
                r024car AS c ON f.codcar = c.codcar
            JOIN 
                r016orn AS o ON f.taborg = o.taborg AND f.numloc = o.numloc
            JOIN 
                r010sit AS s ON f.sitafa = s.codsit
            INNER JOIN 
                r034FOT AS fot ON f.numcad = fot.numcad
                AND f.numemp = fot.numemp
                AND f.tipcol = fot.tipcol
            WHERE 
                f.sitafa = 1
                AND MONTH(f.datadm) = MONTH(GETDATE()) 
                AND YEAR(f.datadm) = YEAR(GETDATE())
        )
        SELECT 
            [Nome Funcionario],
            [Departamento],
            [Cargo],
            [Data de Admissao],
            [Empresa],
            Fotografia
        FROM 
            CTE
        WHERE 
            rn = 1
        ORDER BY 
            [Nome Funcionario];
    """
    
    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in data]
        
        for result in results:
            if result['Fotografia']:
                try:
                    # Verifique se a fotografia é bytes antes de tentar codificá-la
                    if isinstance(result['Fotografia'], (bytes, bytearray)):
                        result['Fotografia'] = 'data:image/jpeg;base64,' + base64.b64encode(result['Fotografia']).decode('utf-8')
                except Exception as e:
                    print(f"Erro ao codificar a imagem: {e}")
                    result['Fotografia'] = None

    return render_template('Novos_Colaboradores.html', results=results)

@app.route('/Nossa_Lideranca')
def index_Nossa_Lideranca():
    query = """ 
        WITH CTE AS (
            SELECT 
        f.nomfun AS [Nome Funcionario],
        (CASE 
            WHEN f.numemp = 4 AND f.codfil = 1 THEN 'Belém'
            WHEN f.numemp = 600 AND f.codfil = 4 THEN 'Limeira'
            WHEN f.numemp = 4 AND f.codfil = 4 THEN 'São Paulo'
            WHEN f.numemp = 2 AND f.codfil = 1 THEN 'Tailandia'
            WHEN f.numemp = 2 AND f.codfil = 4 THEN 'Tailandia'
            WHEN f.numemp = 2 AND f.codfil = 7 THEN 'Tailandia'
            WHEN f.numemp = 2 AND f.codfil = 6 THEN 'Tailandia'
            ELSE e.apeemp
        END) AS [Empresa],
        c.titcar AS [Cargo],
        f.datadm AS [Data de Admissao],
        fot.fotemp AS [Fotografia],
        ROW_NUMBER() OVER (PARTITION BY f.nomfun ORDER BY f.datadm DESC) AS rn
            FROM 
                r034fun AS f
            JOIN 
                r030emp AS e ON f.numemp = e.numemp
            JOIN 
                r024car AS c ON f.codcar = c.codcar
            JOIN 
                r016orn AS o ON f.taborg = o.taborg AND f.numloc = o.numloc
            JOIN 
                r010sit AS s ON f.sitafa = s.codsit
            INNER JOIN 
                r034FOT AS fot ON f.numcad = fot.numcad AND f.numemp = fot.numemp AND f.tipcol = fot.tipcol
            WHERE 
                f.sitafa NOT IN (7, 998, 108, 311, 511,076)
                AND (
                    c.titcar LIKE '%DIRETOR%' OR 
                    c.titcar LIKE '%GERENTE%' OR 
                    c.titcar LIKE '%COORDENADOR%' OR 
                    c.titcar LIKE '%SUPERVISOR%'
                )
                AND c.titcar NOT LIKE '%ANALISTA%'
        )
        
        SELECT 
            [Nome Funcionario],
            [Empresa],
            [Cargo],
            [Data de Admissao],
            [Fotografia]
        FROM 
            CTE
        WHERE 
            rn = 1
        ORDER BY 
            [Nome Funcionario];



    """
    
    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in data]
        
        for result in results:
            if result['Fotografia']:
                try:
                    # Verifique se a fotografia é bytes antes de tentar codificá-la
                    if isinstance(result['Fotografia'], (bytes, bytearray)):
                        result['Fotografia'] = 'data:image/jpeg;base64,' + base64.b64encode(result['Fotografia']).decode('utf-8')
                except Exception as e:
                    print(f"Erro ao codificar a imagem: {e}")
                    result['Fotografia'] = None

    return render_template('Nossa_Lideranca.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
