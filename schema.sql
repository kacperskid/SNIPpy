CREATE TABLE SNP (id_snp INTEGER NOT NULL, name TEXT NOT NULL, seq5 TEXT, seq3 TEXT, alleles TEXT NOT NULL, chrom INTEGER, pos TEXT, Gene_name TEXT, PRIMARY KEY (id_snp));
CREATE TABLE "disease" (
	`id_disease`	INTEGER NOT NULL,
	`disease_name`	TEXT NOT NULL,
	`description`	TEXT,
	`effect`	TEXT NOT NULL,
	PRIMARY KEY(id_disease)
);

CREATE TABLE disease_snp (id_disease_snp INTEGER PRIMARY KEY UNIQUE NOT NULL, disease_snp_id_disease REFERENCES disease (id_disease), disease_snp_snp_id REFERENCES SNP (id_snp));

CREATE TABLE "permissions" (
	`Id_permission`	INTEGER NOT NULL,
	`Permission`	TEXT NOT NULL,
	`Permission_description`	TEXT,
	PRIMARY KEY(Id_permission)
);

CREATE TABLE user (id INTEGER NOT NULL UNIQUE, Login TEXT NOT NULL UNIQUE, Password TEXT NOT NULL UNIQUE, id_perm REFERENCES permissions (Id_permission), PRIMARY KEY (id));