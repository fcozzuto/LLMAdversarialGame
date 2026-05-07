def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    if not resources:
        return [0, 0]

    turn = int(observation.get("turn_index", 0) or 0)
    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    k = turn % len(moves)
    moves = moves[k:] + moves[:k]

    # Pick target: if we can contest, choose resource where we are closer (opp-self). Otherwise, choose resource minimizing opponent distance.
    best = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        contest = (od - sd)
        if contest > 0:
            key = (0, -contest, sd, od, rx, ry)  # want largest (od-sd) => smallest -contest
        else:
            key = (1, od, sd, rx, ry)          # we aren't closer => minimize opponent distance to intercept
        if best is None or key < best[0]:
            best = (key, rx, ry)

    _, tx, ty = best

    old_sd = md(sx, sy, tx, ty)
    old_od = md(ox, oy, tx, ty)

    # Greedy 1-step: maximize our distance reduction and opponent distance increase (move keeps opponent fixed; still works as interception)
    best_m = (None, -10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nsd = md(nx, ny, tx, ty)
        nd_opponent = old_od  # opponent doesn't move in our evaluation; use effect only from our move via blocking/interception proxy: target distance from our new position and our proximity to opponent line.
        # Proxy blocking: if our move brings us closer to opponent position while also moving toward target, more likely to deny.
        block = -md(nx, ny, ox, oy) + (md(sx, sy, ox, oy) if turn % 2 == 0 else 0)
        val = (old_sd - nsd) * 4 + (nd_opponent - old_od) + block * 0.5
        if val > best_m[1]:
            best_m = ((dx, dy), val)

    if best_m[0] is None:
        return [0, 0]
    return [int(best_m[0][0]), int(best_m[0][1])]