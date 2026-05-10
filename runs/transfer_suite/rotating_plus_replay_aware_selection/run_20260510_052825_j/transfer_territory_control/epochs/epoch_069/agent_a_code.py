def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation.get("self_position", (0, 0))
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []) if p is not None and len(p) >= 2)
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells") or []) if p is not None and len(p) >= 2)
    selfT = set((p[0], p[1]) for p in (observation.get("self_territory") or []) if p is not None and len(p) >= 2)
    oppT = set((p[0], p[1]) for p in (observation.get("opponent_territory") or []) if p is not None and len(p) >= 2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort()

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    if not unclaimed and not oppT:
        return [0, 0]

    opp_list = list(oppT) if oppT else []
    un_list = list(unclaimed) if unclaimed else []

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def adj_opponent(nx, ny):
        for ax, ay in ((nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1)):
            if (ax, ay) in oppT:
                return 1
        return 0

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        if (nx, ny) in unclaimed:
            val += 35
        if (nx, ny) in oppT:
            val += 18
        if (nx, ny) in selfT:
            val += 2

        if un_list:
            dmin = 10**9
            for u in un_list:
                d = abs(u[0] - nx) + abs(u[1] - ny)
                if d < dmin:
                    dmin = d
            val += max(0, 20 - dmin)

        if opp_list:
            dopp = 10**9
            for o in opp_list:
                d = abs(o[0] - nx) + abs(o[1] - ny)
                if d < dopp:
                    dopp = d
            if (nx, ny) not in oppT:
                val -= 4 * max(0, 3 - dopp)  # avoid getting herded unless we can flip

        val -= 6 * adj_opponent(nx, ny) if (nx, ny) not in oppT else 0

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]