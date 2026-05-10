def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("catch" in self_role) or ("hunter" in self_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def distc(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0), (-1, -1), (1, -1), (1, 1), (-1, 1), (0, 0)]

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_op = distc(nx, ny, ox, oy)

        if pursuer:
            # Greedy cornering: reduce Chebyshev distance; prefer aligning toward opponent.
            align = (1 if (ox - nx == 0) or (oy - ny == 0) else 0)  # getting on same row/col helps wall-running evasion
            # Slightly penalize being adjacent to obstacles to avoid pinning.
            adj_obs = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if (nx + ax, ny + ay) in obstacles:
                        adj_obs += 1
            score = d_op * 10 - align * 3 + adj_obs * 0.3
            if best is None or score < best_score:
                best = (dx, dy)
                best_score = score
        else:
            # Evader: maximize Chebyshev distance; avoid pushing into obstacles/boundaries.
            adj_obs = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if (nx + ax, ny + ay) in obstacles:
                        adj_obs += 1
            # Prefer moves that increase at least one coordinate away from pursuer (breaks ties deterministically).
            away = 0
            if ox > nx:
                away += 1
            elif ox < nx:
                away += 1
            if oy > ny:
                away += 1
            elif oy < ny:
                away += 1
            score = -d_op * 10 + adj_obs * 0.3 - away * 0.05
            if best is None or score < best_score:
                best = (dx, dy)
                best_score = score

    if best is not None:
        return [int(best[0]), int(best[1])]

    # If blocked entirely, deterministically try a fallback preference order.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(dx), int(dy)]
    return [0, 0]