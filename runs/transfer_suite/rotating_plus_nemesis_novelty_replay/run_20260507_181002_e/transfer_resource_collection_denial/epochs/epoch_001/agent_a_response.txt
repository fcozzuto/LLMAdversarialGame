def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)
    resources = observation.get("resources", [])

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        best = None
        best_d = None
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if best_d is None or d < best_d:
                best_d = d
                best = (rx, ry)
        tx, ty = best
        step_options = []
        dx0 = 0 if tx == sx else (1 if tx > sx else -1)
        dy0 = 0 if ty == sy else (1 if ty > sy else -1)
        candidates = [(dx0, dy0), (dx0, 0), (0, dy0), (dx0, -dy0), (-dx0, dy0), (0, 0)]
        if dx0 != 0 and dy0 != 0:
            candidates += [(-dx0, -dy0), (dx0, -dy0), (-dx0, dy0)]
        # Ensure unique-ish deterministic order
        seen = set()
        for dx, dy in candidates:
            if (dx, dy) in seen: 
                continue
            seen.add((dx, dy))
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                score = cheb(nx, ny, tx, ty)
                # Slightly prefer moves that reduce distance vs opponent too (tie-break)
                opp_bonus = cheb(nx, ny, ox, oy)  # lower is better
                step_options.append((score, opp_bonus, dx, dy))
        if step_options:
            step_options.sort()
            return [int(step_options[0][2]), int(step_options[0][3])]

        # Fallback: choose any legal move minimizing distance to target
        legal = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                    legal.append((cheb(nx, ny, tx, ty), dx, dy))
        legal.sort()
        return [int(legal[0][1]), int(legal[0][2])] if legal else [0, 0]
    else:
        # No resources visible: stay put (deterministic)
        return [0, 0]