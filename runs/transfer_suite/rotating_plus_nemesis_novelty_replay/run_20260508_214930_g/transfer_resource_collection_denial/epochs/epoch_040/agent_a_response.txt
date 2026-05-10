def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (None, -10**9, (0, 0))  # (target, score, move)
    for tx, ty in res:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Encourage taking resources we can reach first; if opponent is closer, still allow if we can "shadow" the race.
        race = (od - sd)
        # Prefer closer targets when race is similar.
        close = -sd
        # Tie-break: resources in our general direction (reduce heading reversal).
        dir_bias = -abs(tx - sx) - abs(ty - sy) + (1 if (tx - sx) * (ox - sx) <= 0 else 0)
        score = race * 10 + close + dir_bias
        # If resource is likely contested, add a small boost for it.
        if od <= sd + 1:
            score += 7
        if score > best[1]:
            best = ( (tx, ty), score, None)

    tx, ty = best[0]
    # Move selection: greedily step that maximizes progress while minimizing opponent opportunity and obstacle risk.
    best_move = [0, 0]
    best_val = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        my_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # Opponent opportunity: how much closer we are vs opponent after our move.
        val = (opp_d - my_d) * 12 - my_d
        # Small penalty if we drift away from the target.
        val -= (abs(tx - nx) + abs(ty - ny)) * 0.2
        # If we are close to the target, slightly favor staying on it.
        if my_d == 0:
            val += 200
        # If stepping blocks immediate approach near opponent (race mitigation), add bonus based on relative improvement.
        if cheb(nx, ny, tx, ty) < cheb(sx, sy, tx, ty):
            val += 6
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]