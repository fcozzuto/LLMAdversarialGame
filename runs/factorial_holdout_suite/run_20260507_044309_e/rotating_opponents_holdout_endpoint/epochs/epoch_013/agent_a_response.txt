def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_target_from(x, y):
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = man(x, y, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer in Manhattan terms
            # encourage tie-break by closer self and by being ahead
            key = (-adv, sd, abs(rx - x), abs(ry - y), rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry, sd, od, adv)
        return best  # (rx,ry,sd,od,adv) or None

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        tgt = best_target_from(nx, ny)
        if tgt is None:
            continue
        rx, ry, sd, od, adv = tgt
        # local obstacle pressure around next position
        neigh_block = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obstacles:
                    neigh_block += 1
        # prefer taking/winning race: large adv, then reduce distance, then reduce opponent reach
        score = (-adv, sd, od, neigh_block, rx, ry)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move