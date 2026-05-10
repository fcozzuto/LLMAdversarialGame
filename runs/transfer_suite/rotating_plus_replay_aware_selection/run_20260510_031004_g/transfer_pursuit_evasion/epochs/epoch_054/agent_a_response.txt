def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    if "evad" in self_role:
        self_is_evader = True
    elif "evad" in opponent_role:
        self_is_evader = False
    else:
        self_is_evader = False

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy)) if self_is_evader else (ox, oy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = None

    def dist_opp(nx, ny):
        return max(abs(nx - ox), abs(ny - oy))  # Chebyshev

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        dopp = dist_opp(nx, ny)
        dman = abs(nx - ox) + abs(ny - oy)
        dtar = abs(nx - target[0]) + abs(ny - target[1])

        if self_is_evader:
            # keep far from pursuer; also run toward the farthest corner unless it reduces distance too much
            val = (dopp * 1000) + (dtar * 3) - (dman)
            # wall-run bias: prefer moves that increase separation in the dominant axis
            val += (1 if (abs(nx - ox) > abs(ny - oy) and (nx - ox) * (ox - sx) >= 0) else 0) * 2
        else:
            # pursue: minimize distance; break ties by moving toward the opponent and away from obstacles near the move
            val = (-dopp * 1000) + (-dman) - dtar
            # slight penalty if adjacent to obstacles (to avoid getting trapped)
            adj_obs = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    x2, y2 = nx + ax, ny + ay
                    if (x2, y2) in obs:
                        adj_obs += 1
            val -= adj_obs * 2

        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)
    return [int(best[0]), int(best[1])]