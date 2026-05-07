def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    occ = set((x, y) for x, y in obstacles)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def opp_corner_target():
        tx = 0 if ox > sx else w - 1
        ty = 0 if oy > sy else h - 1
        return tx, ty

    def best_move_no_resources():
        tx, ty = opp_corner_target()
        best_s, best_m = -10**9, [0, 0]
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in occ:
                continue
            d = cheb(nx, ny, tx, ty)
            s = -d
            if s > best_s:
                best_s, best_m = s, [dx, dy]
        return best_m

    if not resources:
        return best_move_no_resources()

    best_s, best_m = -10**18, [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        # If standing on a resource now, strongly prefer it.
        on_res = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                on_res = 1
                break

        # Evaluate move by best reachable resource advantage over opponent.
        best_adv = -10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)

            # Favor winning race to the resource; denier penalty if opponent is closer.
            # Use tighter tie-breaking toward smaller ds.
            if ds == 0:
                adv = 10**6 - do
            else:
                closeness = -ds
                denier = 4 if do < ds else (0 if do == ds else -2)
                adv = closeness * 10 + (6 if do > ds else -6) + denier + (1 if ds == 1 else 0)

            if adv > best_adv:
                best_adv = adv

        # Small bias: move away from obstacles not needed; keep determinism via on_res and best_adv.
        s = on_res * 10**5 + best_adv
        if s > best_s:
            best_s, best_m = s, [dx, dy]

    return best_m