def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    turn = observation.get("turn_index", 0)

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    # Precompute a small set of nearest unclaimed distances for speed (deterministic: fixed order)
    un_list = list(unclaimed)
    nearest_un = []
    if un_list:
        un_list.sort(key=lambda p: (p[0], p[1]))
        for p in un_list[:12]:
            nearest_un.append(p)

    best = (0, 0)
    best_score = -10**18

    for i, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        score = 0.0
        pt = (nx, ny)

        if pt in opp_t:
            score += 140.0
        elif pt in unclaimed:
            score += 70.0
        elif pt in self_t:
            score += 8.0

        # Frontier bonus: step adjacent to our territory when taking unclaimed
        if pt in unclaimed:
            adj_ours = 0
            for ax, ay in [(nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1)]:
                if (ax, ay) in self_t:
                    adj_ours += 1
            score += 22.0 * (adj_ours > 0) + 6.0 * min(2, adj_ours)

        # Prefer moves that go toward unclaimed (via nearest-unclaimed proxy)
        if un_list:
            mind = 10**9
            for p in nearest_un:
                d = abs(nx - p[0]) + abs(ny - p[1])
                if d < mind:
                    mind = d
            score += 6.0 / (1 + mind)

        # Avoid opponent pressure; territory sweepers punish proximity
        score -= 0.9 * dist((nx, ny), (ox, oy))

        # Tiny deterministic tie-break
        score += 0.001 * ((i + (turn % 7)) % 9)

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]