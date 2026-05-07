def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h:
            res.append((x, y))
    if not res:
        return [0, 0]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_mv = [0, 0]
    best_sc = -10**18

    # One-step anticipatory "race" + denial: favor moves that let us be as early (or earlier) than opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            nx, ny = sx, sy  # deterministic: treat blocked as staying
        sc = 0
        # Immediate pickup is dominant
        picked = 0
        for rx, ry in res:
            if rx == nx and ry == ny:
                picked = 1
                break
        if picked:
            return [dx, dy]

        # Evaluate best contestable resource from next position
        min_self = 10**9
        best_gap = -10**9
        any_contestable = False
        for rx, ry in res:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            gap = opp_d - self_d
            if self_d <= opp_d:
                any_contestable = True
                if gap > best_gap:
                    best_gap = gap
            if self_d < min_self:
                min_self = self_d
        if any_contestable:
            sc = 1000 * best_gap - 5 * min_self
        else:
            # If we can't win any right now, push toward the resource the opponent is closest to.
            # This is a denial move: reduce their easiest option by getting in the way sooner.
            opp_best = -10**9
            for rx, ry in res:
                self_d = cheb(nx, ny, rx, ry)
                opp_d = cheb(ox, oy, rx, ry)
                # Prefer cells that shrink opponent lead the most.
                opp_best = max(opp_best, (self_d - opp_d))
            sc = -200 * opp_best - 2 * min_self

        # Mild tie-break toward staying away from the opponent (reduces accidental interceptions by them).
        sc -= 0.01 * cheb(nx, ny, ox, oy)

        if sc > best_sc:
            best_sc = sc
            best_mv = [dx, dy]

    return best_mv