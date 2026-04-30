def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs_set = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in obs_set

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def obs_pen(x, y):
        if not obs_set:
            return 0.0
        md = 99
        for px, py in obs_set:
            d = cheb(x, y, px, py)
            if d < md:
                md = d
            if md == 0:
                break
        if md <= 1:
            return 3.5
        if md == 2:
            return 1.2
        return 0.0

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    # Prefer: get closer to a resource (especially if we can arrive sooner),
    # keep some distance from opponent, and avoid obstacles.
    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        d_to_opp = cheb(nx, ny, ox, oy)
        min_d_res = 99
        min_res_score = 0.0
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < min_d_res:
                min_d_res = d
                min_res_score = 1.0 / (d + 1.0)
            elif d == min_d_res:
                min_res_score = max(min_res_score, 1.0 / (d + 1.0))

        # If we are very close to the best resource, slightly reward capturing.
        close_bonus = 0.0 if resources == [] else (4.0 if min_d_res <= 0 else (2.0 if min_d_res == 1 else 0.0))

        # Competitive timing: compare how much closer we are than the opponent would be.
        better_than_opp = 0.0
        if resources:
            # Approx with nearest resource: if opponent is farther to its nearest too, we gain.
            # Compute nearest-resource distances for both at this candidate.
            opp_min = 99
            for rx, ry in resources:
                od = cheb(ox, oy, rx, ry)
                if od < opp_min:
                    opp_min = od
            if opp_min < 99:
                better_than_opp = (opp_min - min_d_res) * 1.3

        # Obstacle proximity penalty (want lower, but subtracting means higher penalty reduces value)
        val = 0.0
        if resources:
            val += (6.0 / (min_d_res + 1.0)) + min_res_score * 2.0
        val += better_than_opp + close_bonus
        val += (d_to_opp * 0.35)  # stay farther to reduce contest
        val -= obs_pen(nx, ny) * 1.1

        # Deterministic tie-break: prefer moves with smaller dx^2+dy^2 then lexicographic.
        if val > best_val:
            best_val = val
            best = [dx, dy]
        elif val == best_val and best is not None:
            if dx*dx + dy*dy < best[0]*best[0] + best[1]*best[1]:
                best = [dx, dy]
            elif dx*dx + dy*dy == best[0]*best[0] + best[1]*best[1]:
                if (dx, dy) < (best[0], best[1]):
                    best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]