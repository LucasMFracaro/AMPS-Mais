USE AMPS;

CREATE TABLE contas_resp
(
    cpf VARCHAR(11) PRIMARY KEY,
    senha VARCHAR NOT NULL,
    nome VARCHAR(50) NOT NULL,
    endereco VARCHAR(50) NOT NULL,
    cep VARCHAR(8) NOT NULL,
    bairro VARCHAR(20) NOT NULL,
    cidade VARCHAR(40) NOT NULL,
    uf CHAR(2) NOT NULL,
    nascimento DATE NOT NULL,
    sexo CHAR(1) NOT NULL,
    etnia VARCHAR(15) NOT NULL
);

CREATE TABLE extra
(
    cpf_resp VARCHAR(11),
    num_moradores INT NOT NULL,
    renda_perc DECIMAL(10, 2) NOT NULL,
    especie_dom CHAR(1) NOT NULL,
    tipo_dom CHAR(1) NOT NULL,
    parentesco_resp TINYINT NOT NULL DEFAULT 1,
    FOREIGN KEY(cpf_resp) REFERENCES contas_resp(cpf) ON DELETE CASCADE
);

CREATE TABLE menor
(
    tem_menor TINYINT NOT NULL DEFAULT 0,
    cpf_resp VARCHAR(11),
    idade TINYINT,
    creche BOOLEAN,
    pre_escola BOOLEAN,
    fundamental BOOLEAN,
    ensino_medio BOOLEAN,
    condicao_especial VARCHAR(255),
    FOREIGN KEY (cpf_resp) REFERENCES contas_resp(cpf) ON DELETE CASCADE
);

CREATE TABLE idoso
(
    tem_idoso TINYINT NOT NULL DEFAULT 0,
    cpf_resp VARCHAR(11),
    idade SMALLINT,
    aposentado BOOLEAN,
    bpc BOOLEAN,
    FOREIGN KEY (cpf_resp) REFERENCES contas_resp(cpf) ON DELETE CASCADE
);

