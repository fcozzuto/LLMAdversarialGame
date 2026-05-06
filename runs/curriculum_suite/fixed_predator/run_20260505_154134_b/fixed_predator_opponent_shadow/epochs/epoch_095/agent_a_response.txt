def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

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

    def best_resource_for(posx, posy):
        # choose opponent-nearest as a contest target
        best = None
        best_key = None
        for rx, ry in resources:
            d = cheb(posx, posy, rx, ry)
            key = (d, rx + ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    contx, conty = best_resource_for(ox, oy)

    cand_moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                cand_moves.append((dx, dy))

    def move_score(nx, ny):
        # Contest opponent's nearest first; otherwise maximize "opponent farther than me"
        my_to_cont = cheb(nx, ny, contx, conty)
        opp_to_cont = cheb(ox, oy, contx, conty)
        contest = 8 * (opp_to_cont - my_to_cont) - my_to_cont

        best_gap = -10**9
        best_self = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            gap = oppd - myd
            if gap > best_gap or (gap == best_gap and myd < best_self):
                best_gap = gap
                best_self = myd
        # Encourage also getting close to some resource when gaps tie
        return contest + 3 * best_gap - best_self

    best_move = [0, 0]
    best_val = None
    for dx, dy in cand_moves:
        nx, ny = sx + dx, sy + dy
        val = move_score(nx, ny)
        tie = (val, -cheb(nx, ny, contx, conty), nx, ny, dx, dy)
        if best_val is None or tie > best_val:
            best_val = tie
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]