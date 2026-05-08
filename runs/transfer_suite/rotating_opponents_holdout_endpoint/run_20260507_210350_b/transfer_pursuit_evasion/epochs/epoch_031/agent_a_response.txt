def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(p) for p in (observation.get("resources", []) or [])]
    role = str(observation.get("self_role", "")).lower() + " " + str(observation.get("opponent_role", "")).lower()
    want_escape = any(k in role for k in ("evader", "evade", "runner", "flee", "evasion"))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return in_bounds(x, y) and (x, y) not in obstacles
    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obstacle_density(x, y):
        cnt = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obstacles:
                cnt += 1
        return cnt

    def best_resource_bonus(nx, ny):
        if not resources:
            return 0.0
        dmin = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < dmin: dmin = d
        return 0.0 if dmin == 10**9 else (-1.0 / (1 + dmin))

    best = (0, 0)
    best_score = None

    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        dens = obstacle_density(nx, ny)
        res_bonus = best_resource_bonus(nx, ny)

        # Greedy pursuit with "keep pressure" and "avoid getting boxed" bias.
        if want_escape:
            # Evader: maximize distance, but avoid moving into tight/boxed cells.
            score = (2.2 * d_opp) - (0.9 * dens) + (0.4 * (nx == sx or ny == sy)) + (0.2 * res_bonus)
        else:
            # Pursuer: minimize distance; avoid squares that are surrounded by obstacles.
            score = (-2.4 * d_opp) - (1.0 * dens) + (0.35 * (nx == ox and ny == oy)) + (0.2 * res_bonus)

        # Deterministic tie-break: prefer moves that reduce/stabilize distance first, then x, then y.
        if best_score is None:
            best_score = score
            best = (mdx, mdy)
        else:
            if score > best_score:
                best_score = score
                best = (mdx, mdy)
            elif score == best_score:
                curd = cheb(sx + best[0], sy + best[1], ox, oy)
                cand = cheb(nx, ny, ox, oy)
                if cand < curd or (cand == curd and (mdx, mdy) < best):
                    best = (mdx, mdy)

    return [int(best[0]), int(best[1])]