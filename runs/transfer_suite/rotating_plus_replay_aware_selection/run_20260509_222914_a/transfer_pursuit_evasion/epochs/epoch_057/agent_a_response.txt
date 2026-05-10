def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = any(k in self_role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def corner_target():
        # For evader: pick corner farthest (manhattan) from pursuer with obstacle-adjacent penalty
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        bestv = None
        for cx, cy in corners:
            d = abs(cx - ox) + abs(cy - oy)
            adj = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if (cx + ax, cy + ay) in obstacles:
                        adj += 1
            v = d - 2.0 * adj
            if bestv is None or v > bestv:
                bestv, best = v, (cx, cy)
        return best if best is not None else (w - 1, h - 1)

    tx, ty = (corner_target() if not is_pursuer else None)

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy  # engine keeps us in place if invalid

        # obstacle proximity penalty (discourages sliding into clutter)
        prox = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in obstacles:
                    prox += 1

        d_opp = abs(nx - ox) + abs(ny - oy)

        if is_pursuer:
            # chase while avoiding corners that might let evader escape; also avoid getting too close to obstacles
            score = -d_opp - 0.4 * prox
            # small tie-break to continue roughly toward opponent
            score += -0.02 * ((nx - sx) - (ox - sx)) ** 2 * 0.0
        else:
            # run to chosen corner; also maximize distance from opponent
            d_tar = abs(nx - tx) + abs(ny - ty)
            score = 1.3 * d_opp + 0.8 * d_tar - 0.5 * prox

        if best_score is None:
            best_score = score
            best_move = [dx, dy]
        else:
            if score > best_score + 1e-9:
                best_score = score
                best_move = [dx, dy]
            elif abs(score - best_score) <= 1e-9:
                # deterministic tie-break: prefer moves that change position (stay last)
                if best_move == [0, 0] and [dx, dy] != [0, 0]:
                    best_move = [dx, dy]
                elif best_move != [0, 0] and [dx, dy] == [0, 0]:
                    pass
                else:
                    # lexical preference
                    if (dx, dy) < (best_move[0], best_move[1]):
                        best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]