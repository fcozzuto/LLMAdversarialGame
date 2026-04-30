def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(x, y) for x, y in obstacles}

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    def obst_pen(x, y):
        pen = 0
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d == 0:
                pen += 10**7
            elif d == 1:
                pen += 600
            elif d == 2:
                pen += 60
        return pen

    def choose_target():
        best = None
        bestv = -10**18
        for rx, ry in resources:
            if (rx, ry) in blocked:
                continue
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive is good
            # Encourage taking resources opponent is near if we can still arrive competitive.
            threat = (0 if od > sd else (sd - od + 1))  # larger when opponent is ahead
            v = adv * 1000 - threat * 200 - obst_pen(rx, ry)
            if best is None or v > bestv:
                bestv = v
                best = (rx, ry)
        return best if best is not None else resources[0]

    tx, ty = choose_target()

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    bestm = (0, 0)
    bests = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue

        sd_now = cheb(nx, ny, tx, ty)
        od_now = cheb(ox, oy, tx, ty)
        gain = (od_now - sd_now) * 1000

        # Greedy alignment bonus toward target
        align = 0
        if tx == nx and ty == ny:
            align += 20000
        else:
            step_dx = 0 if tx == nx else (1 if tx > nx else -1)
            step_dy = 0 if ty == ny else (1 if ty > ny else -1)
            align = 220 - (0 if dx == step_dx else 120) - (0 if dy == step_dy else 120)

        # If we are behind opponent for this target, move to reduce their potential by contesting.
        behind = cheb(sx, sy, tx, ty) - cheb(ox, oy, tx, ty)
        contest = 0
        if behind < 0:
            contest = (sd_now <= cheb(ox, oy, tx, ty)) * 800 - (sd_now > cheb(ox, oy, tx, ty)) * 200

        s = gain + align + contest - obst_pen(nx, ny)
        if s > bests:
            bests = s
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]