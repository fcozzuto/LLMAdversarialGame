def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # If we're on a resource, just keep moving toward best next (engine likely handles pickup).
    # Choose nearest resource by squared distance from self (deterministic).
    best = None
    best_d = None
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        d = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
        if best is None or d < best_d or (d == best_d and (rx, ry) < best):
            best = (rx, ry)
            best_d = d

    # If no resources, move toward opponent to limit options (deterministic: towards opponent).
    if best is None:
        tx, ty = ox, oy
    else:
        tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    candidates = []

    # Prefer diagonal/greedy move toward target, then axis-only moves, then staying.
    candidates.append((dx, dy))
    candidates.append((dx, 0))
    candidates.append((0, dy))
    candidates.append((dx, -dy))
    candidates.append((-dx, dy))
    candidates.append((0, 0))

    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if mx not in (-1, 0, 1) or my not in (-1, 0, 1):
            continue
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue
        # Break ties by preferring moves that reduce distance to the target.
        # Deterministic order in candidates already helps; this is just final sanity.
        if best is None:
            return [mx, my]
        nd = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        if best_d is None or nd <= best_d or (mx, my) == candidates[0]:
            return [mx, my]

    return [0, 0]