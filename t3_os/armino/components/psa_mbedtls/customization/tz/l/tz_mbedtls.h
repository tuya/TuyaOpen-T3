#ifndef TZ_MBEDTLS_H_
#define TZ_MBEDTLS_H_
#include "mbedtls/debug.h"
#include "mbedtls/ssl.h"
#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"
#include "mbedtls/error.h"
//#include "mbedtls/certs.h"
#include "mbedtls/threading.h"
#include <mbedtls/pk.h>
#include <mbedtls/ecp.h>
#include <mbedtls/x509_csr.h>
#include <mbedtls/pem.h>
#include <mbedtls/platform.h>

#define TZ_SYMMETRIC_KEY_IDX          (1)
#define TZ_SOFTAP_KEY_IDX             (2)
#define TZ_ASYMMETRIC_KEY_IDX         (3)


#define ASY_KEYGEN_ECP                (1)

int tz_key_mgt_init(void);
int tz_key_mgt_deinit(void);
int tz_key_storage_erase(void);

void tz_mbedtls_pk_init(mbedtls_pk_context *ctx);
void tz_mbedtls_pk_free(mbedtls_pk_context *ctx);
int tz_mbedtls_asymmetric_keygen(mbedtls_pk_context *pk_key, int key_idx, int type);
int tz_mbedtls_ssl_conf_own_cert(mbedtls_ssl_config *conf,
                                mbedtls_x509_crt *own_cert,
                                int pk_key);

int tz_mbedtls_aes_init(mbedtls_aes_context *ctx);
int tz_mbedtls_aes_free(mbedtls_aes_context *ctx);
int tz_mbedtls_aes_setkey_enc(mbedtls_aes_context *ctx, const unsigned char *key, unsigned int keybits);
int tz_mbedtls_aes_setkey_dec(mbedtls_aes_context *ctx, const unsigned char *key, unsigned int keybits);
int tz_mbedtls_aes_crypt_cbc(
    mbedtls_aes_context *ctx,
    int mode,
    size_t length,
    unsigned char iv[16],
    const unsigned char *input,
    unsigned char *output );
int tz_mbedtls_pk_sign(mbedtls_pk_context *ctx, mbedtls_md_type_t md_alg,
                const unsigned char *hash, size_t hash_len,
                unsigned char *sig, size_t *sig_len,
                int (*f_rng)(void *, unsigned char *, size_t), void *p_rng);
char * tz_key_mgt_get_client_key(int key_idx);
int tz_mbedtls_pk_parse_key(mbedtls_pk_context *pk,
                char *key, size_t keylen,
                const unsigned char *pwd, size_t pwdlen);
int tz_mbedtls_pk_decrypt(mbedtls_pk_context *ctx,
                const unsigned char *input, size_t ilen,
                unsigned char *output, size_t *olen, size_t osize,
                int (*f_rng)(void *, unsigned char *, size_t), void *p_rng);
int tz_symmetric_keygen(int len);
int tz_mbedtls_x509write_csr_set_key(mbedtls_x509write_csr *csr_ctx, mbedtls_pk_context *pk_ctx);
int tz_mbedtls_x509write_csr_pem( mbedtls_x509write_csr *ctx, unsigned char *buf, size_t size,
                       int (*f_rng)(void *, unsigned char *, size_t),
                       void *p_rng );

int tz_set_private_key( int index, unsigned char * key );
int tz_set_public_key( int index, unsigned char *key );
int tz_get_public_key( int index, unsigned char *buf, size_t size );
int tz_get_private_key( int index, unsigned char *buf, size_t size );
int tz_set_symmetric_key( int index, unsigned char * key );
int tz_set_symmetric_key_with_len( int index, unsigned char * key, int len );

int tz_mbedtls_pk_write_pubkey_pem( mbedtls_pk_context *key, unsigned char *buf, size_t size );
int my_random(void *p_rng, unsigned char *output, size_t output_len);
#endif /* TZ_MBEDTLS_H_ */

