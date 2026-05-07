def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    turns = int(observation.get("turns_remaining", 0))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        score = 0.0
        my_closest = 10**9
        opp_closest = 10**9
        for rx, ry in resources:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            my_closest = md if md < my_closest else my_closest
            opp_closest = od if od < opp_closest else opp_closest

            # Bias to grabbing resources first; strong penalty if opponent can arrive sooner.
            if md <= turns and od <= turns:
                if md < od:
                    score += 40.0 + 2.0 * (od - md) - 0.5 * md
                elif md == od:
                    score += 10.0 - 0.5 * md
                else:
                    score -= 45.0 + 2.0 * (md - od) + 0.3 * md
            elif md <= turns:
                score += 20.0 - 0.5 * md
            elif od <= turns:
                score -= 25.0 + 0.3 * od

            # Denial: if opponent is very near a resource, try to move closer too.
            if od <= 2:
                score += 6.0 * (1.0 / (1 + md)) - 1.0 * (1.0 / (1 + od))

        # Small deterministic tiebreakers: move toward center and avoid stepping toward opponent.
        center_dist = abs(nx - cx) + abs(ny - cy)
        opp_dist = cheb(nx, ny, ox, oy)
        score -= 0.25 * center_dist
        score += 0.12 * opp_dist

        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]