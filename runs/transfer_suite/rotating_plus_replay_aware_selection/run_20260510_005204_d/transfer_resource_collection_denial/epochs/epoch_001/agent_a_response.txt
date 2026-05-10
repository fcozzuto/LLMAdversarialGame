def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        # Move toward opponent resource pressure (center bias)
        tx, ty = w // 2, h // 2
    else:
        # Choose nearest resource with deterministic tie-break
        sr = sorted((abs(x - sx) + abs(y - sy), x, y) for x, y in resources)
        tx, ty = sr[0][1], sr[0][2]

    def step_towards(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0), (-dx, dy), (dx, -dy)]
        # Deterministic refinement: try candidate order, pick first non-obstacle within bounds
        best = None
        best_d = None
        for cdx, cdy in candidates:
            nx, ny = sx + cdx, sy + cdy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            d = abs(tx - nx) + abs(ty - ny)
            if best is None or d < best_d or (d == best_d and (cdx, cdy) < best):
                best = (cdx, cdy)
                best_d = d
        return best if best is not None else (0, 0)

    # If target cell itself is an obstacle or invalid, pick next nearest safe resource
    safe_resources = [(abs(x - sx) + abs(y - sy), x, y) for x, y in resources if (x, y) not in obstacles]
    if safe_resources:
        safe_resources.sort()
        _, tx2, ty2 = safe_resources[0]
        return [*step_towards(tx2, ty2)]
    return [*step_towards(w // 2, h // 2)]