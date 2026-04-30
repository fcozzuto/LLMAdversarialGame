def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1), (0, 0), (0, 1),
        (1, -1), (1, 0), (1, 1)
    ]

    # Strategy shift: if we're not contesting, pick opponent-closest resource and prioritize contesting
    # while keeping some distance from opponent to reduce collision/route denial.
    best_t = None
    best_metric = None
    contest = []
    for rx, ry in resources:
        myd = king_dist(sx, sy, rx, ry)
        opd = king_dist(ox, oy, rx, ry)
        if myd <= opd + 1:
            contest.append((rx, ry, opd - myd, myd, opd))
    if contest:
        # maximize how much closer we are (opd - myd); tie-break by smaller myd then lexicographic
        best = contest[0]
        for it in contest[1:]:
            if (it[2], -it[3], -it[4], -it[0], -it[1]) > (best[2], -best[3], -best[4], -best[0], -best[1]):
                best = it
        best_t = (best[0], best[1])
    else:
        # pick resource opponent is closest to (so we must contest), tie-break by lexicographic
        best = resources[0]
        best_opd = king_dist(ox, oy, best[0], best[1])
        for rx, ry in resources[1:]:
            d = king_dist(ox, oy, rx, ry)
            if d < best_opd or (d == best_opd and (rx, ry)