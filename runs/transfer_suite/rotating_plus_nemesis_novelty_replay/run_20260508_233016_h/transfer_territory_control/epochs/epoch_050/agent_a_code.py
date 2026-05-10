def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    opp_pos = tuple(observation.get("opponent_position", (sx, sy)))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Frontier targets: unclaimed cells adjacent to opponent territory; prefer them to counter edge-claim.
    frontier = []
    for ox, oy in opp_terr:
        for dx, dy in dirs:
            nx, ny = ox + dx, oy + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                frontier.append((nx, ny))
    if not frontier:
        # Secondary: nearest unclaimed.
        frontier = list(unclaimed) if unclaimed else [(w // 2, h // 2)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Heavily value direct flips; then contest frontier; otherwise just expand toward it.
        enters_opp = (nx, ny) in opp_terr
        is_unclaimed = (nx, ny) in unclaimed
        dfront = min(man(nx, ny, tx, ty) for tx, ty in frontier[:25]) if frontier else 0
        # Keep distance from opponent position slightly (prevents suicidal edge-contact when flip not possible).
        dop = man(nx, ny, opp_pos[0], opp_pos[1])

        val = 0
        if enters_opp:
            val += 20000
        if is_unclaimed:
            val += 2000
        val += 600 - 100 * dfront
        val += -10 * dop
        # Small bias to not backtrack into our own interior when already inside a line
        if (nx, ny) in self_terr:
            val -= 50

        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]