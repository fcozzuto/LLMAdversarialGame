def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    obs_set = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < gw and 0 <= py < gh:
                obs_set.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs_set:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh) or (nx, ny) in obs_set:
            nx, ny = sx, sy
            dx, dy = 0, 0

        best_adv = -10**9
        best_myd = 10**9
        best_rx = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            if adv > best_adv or (adv == best_adv and (myd < best_myd or (myd == best_myd and (rx < best_rx)))):
                best_adv, best_myd, best_rx = adv, myd, rx

        # Prefer high advantage, then shorter distance, then deterministically smaller delta
        key = (best_adv, -best_myd, -best_rx, -dx, -dy)
        if best is None or key > best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]