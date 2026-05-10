def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)
    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()

    def is_pursuer(role):
        r = role.replace("-", "_")
        return ("purs" in r) or (r == "pursuer")
    def is_evader(role):
        r = role.replace("-", "_")
        return ("evad" in r) or (r == "evader")

    pursuer = is_pursuer(self_role) and not is_evader(self_role)
    if not pursuer and is_pursuer(opp_role):
        pursuer = False
    elif pursuer and not is_evader(self_role):
        pursuer = True
    else:
        pursuer = "purs" in self_role

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Tie-breakers: prefer moves that align on axis, then toward/away from nearest corner.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best = None
    best_key = None
    for dx, dy, nx, ny in candidates:
        d = manhattan(nx, ny, ox, oy)
        ax_align = (nx == ox) or (ny == oy)

        nearest_corner_dist = min(manhattan(nx, ny, cx, cy) for cx, cy in corners)
        if pursuer:
            # capture not immediate (radius 0), so chase closest; keep pressure by aligning axis.
            key = (0 if ax_align else 1, d, nearest_corner_dist)
            # smaller is better; deterministic tie-break by delta order
        else:
            # evade: maximize distance; still prefer axis misalignment and moving toward a corner.
            key = (0 if not ax_align else 1, -d, -nearest_corner_dist)
            # key uses negatives so "smaller" means better for our comparison

        if best is None or key < best_key:
            best = (dx, dy)
            best_key = key

    return [int(best[0]), int(best[1])]