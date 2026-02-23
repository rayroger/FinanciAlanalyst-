"use client";

import { useCallback } from "react";
import { usePlaidLink } from "react-plaid-link";
import { api } from "@/lib/api";

interface Props {
  onSuccess: () => void;
}

export default function PlaidLinkButton({ onSuccess }: Props) {
  const openPlaidLink = useCallback(async () => {
    try {
      const res = await api.createLinkToken();
      const linkToken: string = res.data.link_token;

      // Dynamically create the Plaid Link handler
      const handler = (window as typeof window & {
        Plaid?: {
          create: (config: object) => { open: () => void; destroy: () => void };
        };
      }).Plaid?.create({
        token: linkToken,
        onSuccess: async (public_token: string, metadata: { institution?: { name?: string } }) => {
          await api.exchangeToken(public_token, metadata?.institution?.name);
          onSuccess();
        },
        onExit: (err: unknown) => {
          if (err) console.warn("Plaid Link exited with error", err);
        },
      });
      handler?.open();
    } catch (err) {
      console.error("Failed to open Plaid Link", err);
    }
  }, [onSuccess]);

  return (
    <button
      onClick={openPlaidLink}
      className="bg-brand-600 hover:bg-brand-700 text-white font-medium text-sm px-4 py-1.5 rounded-lg transition-colors"
    >
      Connect Bank
    </button>
  );
}
