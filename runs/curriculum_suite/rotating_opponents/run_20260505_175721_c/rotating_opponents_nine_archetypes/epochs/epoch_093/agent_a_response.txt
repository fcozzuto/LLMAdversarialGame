def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Pick a target we can reach first; if tie, pick one with closer "control" to opponent.
    best_t = resources[0]
    best_score = -10**9
    for tx, ty in resources:
        d1 = cheb(sx, sy, tx, ty)
        d2 = cheb(ox, oy, tx, ty)
        # "win-first" bias + tie-breaker toward central-ish and off a diagonal for stability
        win_first = (d2 - d1) * 50
        tie = -d1 * 3
        center = - (abs(tx - (w - 1) / 2) + abs(ty - (h - 1) / 2)) * 0.5
        diag_bias = -abs((tx - sx) - (ty - sy)) * 0.2
        s = win_first + tie + center + diag_bias
        if s > best_score:
            best_score = s
            best_t = (tx, ty)

    tx, ty = best_t
    # Deterministically choose among the 9 moves: maximize our progress while minimizing letting opponent be closer next.
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    cur_d = cheb(sx, sy, tx, ty)
    cur_od = cheb(ox, oy, tx, ty)
    best_m = (0, 0)
    best_v = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # prefer reducing distance; strongly punish increasing opponent relative advantage
        progress = cur_d - nd
        if nd == cur_d and (dx != 0 or dy != 0):
            progress -= 0.3  # discourage dithering
        opp_next = cur_od  # opponent position fixed this turn; use current for consistent bias
        rel = (opp_next - nd)
        v = progress * 100 + rel * 2
        # small obstacle-avoidance: discourage moves that keep us adjacent to obstacles (local roughness)
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    adj_obs += 1
        v -= adj_obs * 0.2
        if v > best_v:
            best_v = v
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]