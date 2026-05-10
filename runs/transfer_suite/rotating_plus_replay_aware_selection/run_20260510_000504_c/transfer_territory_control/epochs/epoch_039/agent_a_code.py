def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blk(x, y): return (x, y) in obstacles
    def manh(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    # Find a small deterministic set of best unclaimed targets to chase
    un_list = list(unclaimed)
    if un_list:
        ordered = sorted(un_list, key=lambda t: (manh(sx, sy, t[0], t[1]), t[0], t[1]))
        targets = ordered[:16]
    else:
        targets = []

    best_move = (0, 0)
    best_score = -10**18
    opp_edge = set()
    for (x, y) in opp_terr:
        # approximate "edges" by adjacency to unclaimed/self or boundary
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            if (nx, ny) not in opp_terr:
                opp_edge.add((x, y))
                break
    opp_edge = list(opp_edge)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blk(nx, ny):
            continue
        score = 0
        if (nx, ny) in self_terr:
            score += 3
        if (nx, ny) in opp_terr:
            score += 8  # flipping on entry is valuable vs counterclaim
        if (nx, ny) in unclaimed:
            score += 2

        if targets:
            # Closest unclaimed distance after move (lower is better)
            dmin = 10**9
            for tx, ty in targets:
                d = manh(nx, ny, tx, ty)
                if d < dmin:
                    dmin = d
            score += (40 - 5 * dmin)
        else:
            # No unclaimed: push toward opponent territory centroid-ish deterministically
            if opp_edge:
                ax = sum(x for x, _ in opp_edge) // len(opp_edge)
                ay = sum(y for _, y in opp_edge) // len(opp_edge)
                score += (24 - 2 * manh(nx, ny, ax, ay))

        # Extra bias: keep movement efficient (prefer not to increase distance to nearest target)
        if targets:
            dcur = min(manh(sx, sy, tx, ty) for tx, ty in targets)
            dnxt = min(manh(nx, ny, tx, ty) for tx, ty in targets)
            score += (dcur - dnxt) * 6

        # Deterministic tie-break
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    # If all moves were blocked (rare), stay still
    dx, dy = best_move
    return [int(dx), int(dy)]