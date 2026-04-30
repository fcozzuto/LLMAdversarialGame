def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
        best = (0, 0)
        bestv = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = -man(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = (0, 0)
    bestv = -10**18

    # Tie-break toward moves that increase my distance from opponent while still progressing to contested resources.
    base_op_dist = man(sx, sy, ox, oy)

    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny):
            continue

        my_to = man(nx, ny, ox, oy)
        op_progress = my_to - base_op_dist  # prefer moving away (positive)

        best_res = -10**18
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)

            # Want resources where I can get there earlier than opponent (opd - myd large).
            # If I'm already on a resource, heavily prioritize it.
            if nx == rx and ny == ry:
                sc = 10**6
            else:
                sc = (opd - myd) * 1000 - myd * 3

            # If I move into a position that makes the opponent closer to my best target, discourage slightly.
            if opd == 0:
                sc -= 5000

            if sc > best_res:
                best_res = sc

        # Add small deterministic shaping:
        # - encourage stepping closer to the overall nearest resource
        # - reward moving away from opponent slightly
        nearest_my = min(manhattan for manhattan in [man(nx, ny, rx, ry) for rx, ry in resources])
        v = best_res - nearest_my * 1.2 + op_progress * 2.0

        if v > bestv:
            bestv = v
            best = (dxm, dym)

    return [best[0], best[1]]