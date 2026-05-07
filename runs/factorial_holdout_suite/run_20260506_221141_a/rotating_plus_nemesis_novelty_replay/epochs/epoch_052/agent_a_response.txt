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

    def valid(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obs_set

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None  # (score1, score2, tie_x, tie_y, dx, dy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # After this step, evaluate the best resource we could plausibly beat.
        best_adv = None
        best_my_d = None
        for tx, ty in resources:
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            adv = opd - myd
            # Prefer more winning (higher adv), then closer to finish (lower myd), then lexicographic.
            key = (adv, -myd, tx, ty)
            if best_adv is None or key > best_adv:
                best_adv = key
                best_my_d = myd

        # Overall move score: prioritize winning advantage, then quick completion, then moving toward center subtly.
        center_bias = -abs((nx - (gw - 1) / 2)) - abs((ny - (gh - 1) / 2))
        score = (best_adv[0], -best_my_d, center_bias, nx, ny, dx, dy)
        if best is None or score > best:
            best = score

    if best is None:
        return [0, 0]
    return [int(best[-2]), int(best[-1])]