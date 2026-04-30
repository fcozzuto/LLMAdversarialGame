def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    def valid(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles

    # Pick target where we are relatively closer than opponent.
    best_r = resources[0]
    best_key = -10**18
    for rx, ry in resources:
        sd = king_dist(sx, sy, rx, ry)
        od = king_dist(ox, oy, rx, ry)
        key = (od - sd) * 1000 - sd
        # Small tie-break toward nearer resources.
        key -= king_dist(rx, ry, 3.5, 3.5)
        if key > best_key:
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = [0, 0]
    best_sc = -10**18

    # Also consider a secondary target to reduce opponent's easiest capture.
    # Choose a resource that maximizes their potential advantage; we try to deny it.
    opp_likely = resources[0]
    opp_best = -10**18
    for rx, ry in resources:
        od = king_dist(ox, oy, rx, ry)
        sd = king_dist(sx, sy, rx, ry)
        key = (sd - od) * 1000 + od  # high when opponent far ahead; we deny that
        if key > opp_best:
            opp_best = key
            opp_likely = (rx, ry)
    dx2, dy2 = opp_likely

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            sc = -10**15
        else:
            myd = king_dist(nx, ny, tx, ty)
            myd_now = king_dist(sx, sy, tx, ty)
            # Higher is better: reduce distance to our target; increase their distance to it.
            oppd = king_dist(ox, oy, tx, ty)
            oppd_after = king_dist(ox, oy, tx, ty)  # opponent doesn't move now; still include our stance
            sc = (myd_now - myd) * 200 - myd * 3 + (oppd - myd) * 5

            # Denial: move that increases opponent advantage on the likely-denied resource.
            oppd2 = king_dist(ox, oy, dx2, dy2)
            myd2 = king_dist(nx, ny, dx2, dy2)
            sc += (myd2 - oppd2) * 30  # want our distance >= their distance to that resource

            # Extra mild obstacle aversion: penalize if adjacent squares are blocked (helps avoid traps).
            adj_pen = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    px, py = nx + ax, ny + ay
                    if (px, py) in obstacles:
                        adj_pen += 1
            sc -= adj_pen * 2

        if sc > best_sc:
            best_sc = sc
            best_m = [dx, dy]

    return [int(best_m[0]), int(best_m[1])]