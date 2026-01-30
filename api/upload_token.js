import { handleUpload } from '@vercel/blob/client';

export const config = {
    runtime: 'nodejs',
};

export default async function handler(request, response) {
    const body = request.body;

    try {
        const jsonResponse = await handleUpload({
            body,
            request,
            onBeforeGenerateToken: async (pathname /*, clientPayload */) => {
                const token = process.env.BLOB_READ_WRITE_TOKEN;
                if (!token) throw new Error("BLOB_READ_WRITE_TOKEN is not set");

                return {
                    allowedContentTypes: ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'],
                    tokenPayload: JSON.stringify({
                        // optional, sent to your server on upload completion
                    }),
                };
            },
            onUploadCompleted: async ({ blob, tokenPayload }) => {
                console.log('blob upload completed', blob, tokenPayload);
            },
        });

        response.status(200).json(jsonResponse);
    } catch (error) {
        response.status(400).json({ error: error.message });
    }
}
