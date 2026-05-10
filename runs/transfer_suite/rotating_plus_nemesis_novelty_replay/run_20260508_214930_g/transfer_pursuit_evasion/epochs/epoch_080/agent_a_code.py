def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursuer" in role) or ("hunter" in role) or ("seeker" in role)
    is_evader = ("evader" in role) or ("runner" in role) or ("fugitive" in role)
    if not (is_pursuer or is_evader):
        is_pursuer = True
    pursuer = is_pursuer

    obs = set()
    for b in (observation.get("obstacles") or []):
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = dist2(nx, ny)
        center_pen = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        # Small tie-breakers: avoid edges when close decisions matter; prefer diagonal/axis parity deterministically.
        edge_pen = -(min(nx, w - 1 - nx) + min(ny, h - 1 - ny))
        # If pursuing: minimize distance; if evading: maximize distance.
        s = (-d if pursuer else d) + 0.02 * center_pen + 0.01 * edge_pen
        if best is None or s > best or (s == best and (dx, dy) < best_move):
            best = s
            best_move = (dx, dy)

    # If all moves invalid, stay still.
    return [int(best_move[0]), int(best_move[1])]