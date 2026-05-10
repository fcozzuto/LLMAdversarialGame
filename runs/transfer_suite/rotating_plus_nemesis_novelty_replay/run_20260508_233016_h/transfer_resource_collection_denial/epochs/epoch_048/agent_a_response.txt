def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    best_res = None
    best_key = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        # Prefer resources we can reach no later than opponent; otherwise, the least losing option.
        can_win = 0 if myd <= opd else 1
        key = (can_win, abs(myd - opd), myd, -opd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    tiebreak = observation.get("turn_index", 0) % 9

    best_mv = [0, 0]
    best_score = None
    for i, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_dist = cheb(nx, ny, tx, ty)
        if self_dist == 0:
            self_dist_manh = man(nx, ny, tx, ty)
        else:
            self_dist_manh = man(nx, ny, tx, ty)

        opp_dist_now = cheb(ox, oy, tx, ty)
        # Deny: if opponent is close, prioritize moves that increase (or at least not worsen) their lead.
        deny = (opp_dist_now - self_dist)  # larger is better
        # Small deterministic tie-break: rotate preference order by turn_index.
        rot = (i + tiebreak) % 9
        score = (self_dist, self_dist_manh, -deny, rot)
        if best_score is None or score < best_score:
            best_score = score
            best_mv = [dx, dy]

    return best_mv