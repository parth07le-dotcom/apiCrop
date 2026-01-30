import { handleUpload } from '@vercel/blob/client';

export const config = {
    runtime: 'edge',
};

export default async function handler(request) {
    const body = await request.json();

    try {
        const jsonResponse = await handleUpload({
            body,
            request,
            onBeforeGenerateToken: async (pathname /*, clientPayload */) => {
                // Generate a client token for the browser to upload the file
                // ⚠️ Authenticate and authorize users before generating the token.
                // Otherwise, you're allowing anonymous uploads.
                const token = process.env.BLOB_READ_WRITE_TOKEN;
                if (!token) throw new Error("BLOB_READ_WRITE_TOKEN is not set");

                return {
                    allowedContentTypes: ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'],
                    tokenPayload: JSON.stringify({
                        // optional, sent to your server on upload completion
                        // you could pass a user id from auth, or a value from clientPayload
                    }),
                };
            },
            onUploadCompleted: async ({ blob, tokenPayload }) => {
                // Available to the Serverless Function after upload is completed
                // ⚠️ This will be called on every upload
                console.log('blob upload completed', blob, tokenPayload);
            },
        });

        return new Response(JSON.stringify(jsonResponse), {
            status: 200,
            headers: {
                'content-type': 'application/json',
            },
        });
    } catch (error) {
        return new Response(
            JSON.stringify(
                { error: error.message },
            ),
            { status: 400 },
        );
    }
}
