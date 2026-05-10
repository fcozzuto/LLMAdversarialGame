def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # Ensure we stand on a valid tile (shouldn't happen)
    if (sx, sy) in obs:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_mv = (0, 0)
    best_score = -10**9

    for mdx, mdy in deltas:
        nsx, nsy = sx + mdx, sy + mdy
        if not valid(nsx, nsy):
            continue

        # Predict opponent's greedy pursuit move towards our next position
        best_od = (0, 0)
        best_od_dist = 10**9
        for odx, ody in deltas:
            nox, noy = ox + odx, oy + ody
            if not valid(nox, noy):
                continue
            d = cheb(nox, noy, nsx, nsy)
            if d < best_od_dist or (d == best_od_dist and deltas.index((odx, ody)) < deltas.index(best_od)):
                best_od_dist = d
                best_od = (odx, ody)

        odx, ody = best_od
        nox, noy = ox + odx, oy + ody
        if (nox, noy) == (nsx, nsy):
            score = -10**8  # immediate capture (very bad)
        else:
            # Prefer maximizing separation; slight bias to move away from current opponent
            score = best_od_dist * 1000 + cheb(sx, sy, ox, oy) - cheb(nsx, nsy, ox, oy)

        if score > best_score:
            best_score = score
            best_mv = (mdx, mdy)

    return [int(best_mv[0]), int(best_mv[1])]