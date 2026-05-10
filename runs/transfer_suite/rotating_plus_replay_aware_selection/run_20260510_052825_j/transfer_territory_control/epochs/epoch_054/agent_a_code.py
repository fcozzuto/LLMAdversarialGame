def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    # Precompute a small deterministic set of unclaimed targets to keep scoring cheap.
    unclaimed_sorted = sorted(unclaimed)
    targets = unclaimed_sorted[:18] if len(unclaimed_sorted) > 18 else unclaimed_sorted

    def min_dist_to_unclaimed(nx, ny):
        if not targets:
            return 0
        md = 10**9
        for tx, ty in targets:
            d = man(nx, ny, tx, ty)
            if d < md:
                md = d
        return md

    # Prefer expanding into unclaimed near our territory while keeping distance from opponent.
    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        if (nx, ny) in selfT:
            base = 1.0
        elif (nx, ny) in unclaimed:
            base = 6.0
        elif (nx, ny) in oppT:
            base = -4.0
        else:
            base = 0.3

        d_opp = man(nx, ny, ox, oy)
        d_un = min_dist_to_unclaimed(nx, ny)

        # Small deterministic bias toward getting closer to the nearest unclaimed.
        score = base + (0.35 / (1 + d_un)) - (0.03 * d_opp)

        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]