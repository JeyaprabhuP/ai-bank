import React from "react";
import { Navigate } from "react-router-dom";
import { getCurrentUser } from "../services/authService";

/**
 * Blocks access to a route subtree based on the logged-in user's role.
 *
 * `block(user)` returns true when this user should NOT see the routes
 * below — they're redirected to `redirectTo` instead. This is what
 * keeps customers confined to the AI Assistant experience: any attempt
 * to reach the staff dashboard (by clicking a stale link, typing a URL,
 * using browser back/forward, etc.) is redirected straight back to
 * /customer/chat, with no route that leads anywhere else.
 */
export default function RoleRoute({ block, redirectTo, children }) {
  const user = getCurrentUser();
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (block(user)) {
    return <Navigate to={redirectTo} replace />;
  }
  return children;
}
