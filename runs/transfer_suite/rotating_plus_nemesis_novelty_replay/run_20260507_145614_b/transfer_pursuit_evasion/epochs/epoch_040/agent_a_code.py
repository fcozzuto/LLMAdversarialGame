def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    evader = any(k in role for k in ("evader", "escape", "runner", "flee", "evade"))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def neigh_free(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    # Corner preference to reduce being cornered (for evader) / cornering opponent (for pursuer)
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = corners[0]
    best_cd2 = dist2(corners[0][0], corners[0][1], ox, oy)
    for cx, cy in corners[1:]:
        cd2 = dist2(cx, cy, ox, oy)
        if (evader and cd2 > best_cd2) or ((not evader) and cd2 < best_cd2):
            best_corner, best_cd2 = (cx, cy), cd2
    tx, ty = best_corner

    # One-step greedy with obstacle-aware tie-break and (light) anti-aim for pursuer
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_d2 = dist2(nx, ny, ox, oy)

        if evader:
            # Prefer moving away, also towards target corner, and towards safer neighborhoods
            val = (my_d2 * 10.0) + (dist2(nx, ny, tx, ty) * 0.01) + (neigh_free(nx, ny) * 0.1)
            # If moving into capture immediately should be avoided (my_d2==0)
            val -= 1000.0 if my_d2 == 0 else 0.0
        else:
            # Prefer closing distance; prefer moves that also reduce opponent's escape space
            opp_neigh = neigh_free(ox, oy)
            val = (-my_d2 * 10.0) + (neigh_free(nx, ny) * 0.05) + (-opp_neigh * 0.02)
            val += 1000.0 if my_d2 == 0 else 0.0

        # Deterministic tie-break: higher val, then fewer boundary pushes (via preference order by dx,dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]