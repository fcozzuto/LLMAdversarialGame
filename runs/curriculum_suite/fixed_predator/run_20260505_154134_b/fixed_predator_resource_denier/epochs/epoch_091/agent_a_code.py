def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 if d1 > d2 else d2  # Chebyshev

    tx, ty = w // 2, h // 2
    best_move = None
    best_key = None

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy

        if not resources:
            # Prefer center while not stepping into opponent pressure
            myc = dist((nx, ny), (tx, ty))
            oppc = dist((nx, ny), (ox, oy))
            key = (-oppc, myc, nx + ny)
        else:
            # Choose move that creates the biggest "reach advantage" to some remaining resource
            # score = (opp_dist - self_dist) -> larger is better; tie-break on smaller self_dist
            local_best = None
            for rx, ry in resources:
                self_d = dist((nx, ny), (rx, ry))
                opp_d = dist((ox, oy), (rx, ry))
                # Penalize giving opponent very close capture while we are far
                reach_adv = opp_d - self_d
                # Small tiebreaker to prefer earlier progress toward the chosen cell
                cell_prox = self_d
                denier_risk = dist((nx, ny), (ox, oy))
                key2 = (reach_adv, -cell_prox, -denier_risk, -(rx + ry))
                if local_best is None or key2 > local_best[0]:
                    local_best = (key2, (rx, ry))
            # Also discourage moves that are "over-commitment" when already behind for all resources
            key = (local_best[0][0], local_best[0][1], local_best[0][2], local_best[0][3], dist((nx, ny), (tx, ty)), nx + ny)

        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]