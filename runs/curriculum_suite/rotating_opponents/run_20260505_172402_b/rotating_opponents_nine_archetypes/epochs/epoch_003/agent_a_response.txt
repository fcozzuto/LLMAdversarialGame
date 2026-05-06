def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs_set

    def greedy_step(px, py, txs):
        if not txs:
            return px, py
        best = None
        for rx, ry in txs:
            d = abs(rx - px) + abs(ry - py)
            if best is None or d < best[0]:
                best = (d, rx, ry)
        _, rx, ry = best
        dx = 0 if rx == px else (1 if rx > px else -1)
        dy = 0 if ry == py else (1 if ry > py else -1)
        nx, ny = px + dx, py + dy
        if valid(nx, ny):
            return nx, ny
        # fall back: any valid move that decreases distance to chosen resource
        curd = abs(rx - px) + abs(ry - py)
        bestd, bestpos = curd, (px, py)
        for ddx, ddy in moves:
            nx, ny = px + ddx, py + ddy
            if not valid(nx, ny):
                continue
            d = abs(rx - nx) + abs(ry - ny)
            if d < bestd:
                bestd, bestpos = d, (nx, ny)
        return bestpos

    # Predict opponent next position with the same resource-greedy policy (deterministic).
    op_next = greedy_step(ox, oy, resources)
    opnx, opny = op_next

    # Evaluate our candidate moves by how well they secure a resource vs the opponent next step.
    best_score, best_move = -10**9, (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if resources:
            sec = -10**9
            for rx, ry in resources:
                my_d = abs(rx - nx) + abs(ry - ny)
                op_d = abs(rx - opnx) + abs(ry - opny)
                # Prefer winning access to resources; slight center bias to avoid corners lock-in.
                center_bias = -0.02 * ((rx - (w - 1) / 2) ** 2 + (ry - (h - 1) / 2) ** 2)
                val = (op_d - my_d) + center_bias
                if val > sec:
                    sec = val
            # Ensure we don't wander next to obstacles; count nearby obstacles.
            prox = 0
            for ex in (-1, 0, 1):
                for ey in (-1, 0, 1):
                    if (nx + ex, ny + ey) in obs_set:
                        prox += 1
            score = sec - 0.3 * prox
        else:
            # No resources: move toward center while avoiding obstacles.
            score = -((nx - (w - 1) / 2) ** 2 + (ny - (h - 1) / 2) ** 2)
        if score > best_score:
            best_score, best_move = score, (dx, dy)

    dx, dy = best_move
    nx, ny = sx + dx, sy + dy
    if not valid(nx, ny):
        return [0, 0]
    return [dx, dy]