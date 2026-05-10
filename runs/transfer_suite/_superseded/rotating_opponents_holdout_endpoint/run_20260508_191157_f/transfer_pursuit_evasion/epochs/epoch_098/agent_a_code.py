def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    role = observation.get("self_role", "pursuer")
    want_far = (role == "evader")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def min_obst_dist(nx, ny):
        if not obstacles:
            return 999
        m = 999
        for ax, ay in obstacles:
            d = abs(ax - nx) + abs(ay - ny)
            if d < m:
                m = d
                if m == 0:
                    return 0
        return m

    # Prefer moves that change the larger separation axis toward/away from opponent.
    best_move = [0, 0]
    best_score = -10**18 if not want_far else 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist2 = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
        md = min_obst_dist(nx, ny)

        ax = abs(ox - sx)
        ay = abs(oy - sy)
        # Directional term: encourage reducing (pursuer) / increasing (evader) the dominant axis.
        if ax >= ay:
            dom = abs(ox - nx) - abs(ox - sx)  # negative is good for pursuer
            dom_score = -dom if not want_far else dom
        else:
            dom = abs(oy - ny) - abs(oy - sy)
            dom_score = -dom if not want_far else dom

        # Obstacle term: avoid being too close (or, for evader, also avoid close gets blocked).
        # pursuer likes clearance to keep mobility near opponent; evader also likes clearance to dodge walls.
        clear = md
        obst_score = (clear * 0.15)  # higher is better for both sides, since evader can choose routes too

        # Main objective
        main = -dist2 if not want_far else dist2
        score = main + dom_score * 0.35 + obst_score

        if (not want_far and score > best_score) or (want_far and score < best_score):
            best_score = score
            best_move = [dx, dy]

    return best_move