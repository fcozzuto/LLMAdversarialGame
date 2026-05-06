def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    blocked = set((p[0], p[1]) for p in obstacles)

    # If no resources, just move toward opponent to block/collide if allowed
    if not resources:
        tx, ty = ox, oy
    else:
        # Choose target resource: nearest to self; tie-break by farther from opponent
        best = None
        for rx, ry in resources:
            d1 = abs(rx - sx) + abs(ry - sy)
            d2 = abs(rx - ox) + abs(ry - oy)
            # prefer smaller d1, then larger d2, then lexicographic
            key = (d1, -d2, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    candidates = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    valid = []
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            # score by distance to target; slight preference to reduce opponent distance (deny)
            dist = abs(nx - tx) + abs(ny - ty)
            opp_dist = abs(nx - ox) + abs(ny - oy)
            # prefer closer to target, then farther from own to opponent? actually deny: prefer larger opp_dist
            key = (dist, -opp_dist, dx, dy)
            valid.append((key, [dx, dy]))
    if not valid:
        return [0, 0]
    valid.sort(key=lambda t: t[0])
    return valid[0][1]