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
    best = None  # (adv, -self_d, tx, ty, dx, dy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh) or (nx, ny) in obs_set:
            continue

        best_for_move = None  # (adv, self_d, tx, ty)
        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - self_d
            cand = (adv, self_d, rx, ry)
            if best_for_move is None or cand[0] > best_for_move[0] or (cand[0] == best_for_move[0] and (cand[1] < best_for_move[1] or (cand[1] == best_for_move[1] and (cand[2], cand[3]) < (best_for_move[2], best_for_move[3])))):
                best_for_move = cand

        adv, self_d, tx, ty = best_for_move
        key = (adv, -self_d, tx, ty, dx, dy)
        if best is None or (key[0], key[1], key[2], key[3]) > (best[0], best[1], best[2], best[3]):
            best = key

    return [best[4], best[5]]