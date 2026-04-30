def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                resources.append((rx, ry))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx, cy = w // 2, h // 2
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        my_opp_dist = cheb(nx, ny, ox, oy)
        score = my_opp_dist * 1.0  # prefer staying away

        if resources:
            if (nx, ny) in set(resources):
                score += 10000  # immediate pickup

            # choose among resources by "being closer than opponent"
            # compute on the fly; small list size (<=12)
            local = []
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                if myd <= opd:
                    local.append((opd - myd, -myd, rx, ry))
            if not local:
                # if we're not currently advantaged anywhere, go toward the most reachable resource
                for rx, ry in resources:
                    myd = cheb(nx, ny, rx, ry)
                    local.append((-myd, -myd, rx, ry))

            # emphasize few best targets deterministically
            local.sort(reverse=True)
            for k in range(min(4, len(local))):
                adv, negd, rx, ry = local[k]
                d = -negd
                score += adv * 3.5 - d * 0.9
                score += (abs(rx - cx) + abs(ry - cy)) * (-0.02)  # slight center bias
        else:
            score += -cheb(nx, ny, cx, cy) * 0.8

        # tie-break: deterministic preference order (center-ish then away from opponent)
        score += -cheb(nx, ny, cx, cy) * 0.0001

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]