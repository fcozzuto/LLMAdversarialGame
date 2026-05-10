def choose_move(observation):
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles}

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def dist8(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    # Estimate opponent next position when targeting a given resource
    def opp_next(tx, ty):
        best = None
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = dist8(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                best = (nx, ny)
        if best is None:
            return (ox, oy)
        return best

    # Precompute resource positions and sort deterministically
    rpos = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if inb(rx, ry) and (rx, ry) not in obs:
            rpos.append((rx, ry))
    rpos.sort()

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Landing reward
        landing = 0
        for (rx, ry) in rpos:
            if rx == nx and ry == ny:
                landing = 1
                break

        total = landing * 1000 - dist8(nx, ny, ox, oy)  # mild pressure away from opponent
        # Evaluate contest for each resource by estimated 1-step opponent response
        for (rx, ry) in rpos:
            d_our = dist8(nx, ny, rx, ry)
            o1x, o1y = opp_next(rx, ry)
            d_opp = dist8(o1x, o1y, rx, ry)
            adv = d_opp - d_our  # positive means we get closer first
            # Favor resources where we can beat opponent soon; penalize where we fall behind
            if d_our == 0:
                total += 200
            elif adv > 0:
                total += 40 / (1 + d_our)
            elif adv < 0:
                total -= 25 / (1 + d_opp)
            else:
                total -= 5 / (1 + d_our)

        # Tie-break deterministically: prefer (dx,dy) earlier in moves list
        if total > best_val:
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]