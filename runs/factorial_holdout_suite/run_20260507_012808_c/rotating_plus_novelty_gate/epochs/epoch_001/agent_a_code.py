def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = set((x, y) for x, y in obstacles)
    w = observation["grid_width"]
    h = observation["grid_height"]

    if (sx, sy) in obs_set:
        # Shouldn't happen; back off deterministically
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                return [dx, dy]
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best, bestd = [0, 0], 10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                    d = max(abs(nx - tx), abs(ny - ty))
                    if d < bestd:
                        bestd, best = d, [dx, dy]
        return best

    def steps(x1, y1, x2, y2):
        return max(abs(x1 - x2), abs(y1 - y2))

    # Choose a resource we can reach earlier than opponent
    best_r = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        sd = steps(sx, sy, rx, ry)
        od = steps(ox, oy, rx, ry)
        key = (sd - od, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    # If already on a resource, stay
    if sx == rx and sy == ry:
        return [0, 0]

    cur_d = (sx - rx) * (sx - rx) + (sy - ry) * (sy - ry)
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                d = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
                oppd = steps(ox, oy, rx, ry)
                # Prefer moves that reduce distance; slight preference for worsening opponent advantage
                moves.append((d, max(abs(nx - rx), abs(ny - ry)) - oppd, dx, dy, d - cur_d))
    moves.sort(key=lambda t: (t[0], t[1], t[4], t[2], t[3]))
    return [moves[0][2], moves[0][3]]