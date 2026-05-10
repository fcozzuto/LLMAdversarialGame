def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or (sx, sy)
    ox, oy = int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    my_terr = set(map(tuple, observation.get("self_territory") or []))

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0)]
    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Prefer moves into unclaimed cells that are nearest to our position.
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        if (nx, ny) in unclaimed:
            d = abs(nx - sx) + abs(ny - sy)
            t = 100000 - d
        else:
            # Otherwise move to increase distance from opponent if possible, else towards opponent.
            d1 = abs(nx - sx) + abs(ny - sy)
            d2 = abs(nx - ox) + abs(ny - oy)
            t = d2 * 2 - d1
        if best is None or t > best[0]:
            best = (t, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]