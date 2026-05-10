def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role", "") or "").lower()
    evader = ("evader" in role) or ("runner" in role) or ("escape" in role)
    pursuer = ("pursuer" in role) or ("chaser" in role)
    if not (evader or pursuer):
        evader = True

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    def dist(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def clamp_in(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Precompute nearest obstacle distance terms locally (deterministic and small).
    obst_list = list(obs_set)

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_in(nx, ny):
            val = -10**18
        else:
            d2 = dist(nx, ny, ox, oy)
            if obst_list:
                min_obst2 = min(dist(nx, ny, ox2, oy2) for (ox2, oy2) in obst_list)
            else:
                min_obst2 = 0

            # Goal: evade maximize distance, but also avoid obstacles; pursuer minimize distance and
            # prefer obstacle-distant lines to keep mobility.
            if evader:
                val = d2 + 0.15 * min_obst2
                # Mild preference for corners to break zigzag cycles, but not the only objective.
                cx, cy = (0, 0)
                corners = ((0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1))
                # deterministic small corner bias
                cb = 0
                for k, (cx, cy) in enumerate(corners):
                    t = -dist(nx, ny, cx, cy)
                    cb += t if (k % 2 == 0) else t * 0.5
                val += 0.001 * cb
            else:
                val = -d2 + 0.05 * min_obst2
                # Prefer moving toward opponent on x/y if possible (break ties deterministically)
                val += 0.002 * (-(abs((nx - ox)) + abs((ny - oy))))

        if best is None or (val > best_val) or (val == best_val and (dx, dy) < best):
            best = (dx, dy)
            best_val = val

    return [int(best[0]), int(best[1])]