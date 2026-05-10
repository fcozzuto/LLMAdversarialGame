def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def man(x1, y1, x2, y2): 
        dx = x1 - x2; dx = dx if dx >= 0 else -dx
        dy = y1 - y2; dy = dy if dy >= 0 else -dy
        return dx + dy

    frontier = set()
    for (x, y) in self_terr:
        for dx, dy in moves:
            if dx == 0 and dy == 0: 
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in unclaimed and inb(nx, ny):
                frontier.add((nx, ny))

    def best_dist_to(cand, cells):
        if not cells: 
            return 999
        cx, cy = cand
        best = 999
        for tx, ty in cells:
            d = man(cx, cy, tx, ty)
            if d < best: best = d
        return best

    desired_unclaimed = frontier if frontier else unclaimed
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        score = 0
        if (nx, ny) in unclaimed: score += 12
        if (nx, ny) in opp_terr: score += 7
        if (nx, ny) in self_terr: score += 2
        score -= 0.6 * best_dist_to((nx, ny), desired_unclaimed)
        score += 0.12 * (man(nx, ny, ox, oy) )  # prefer staying away from opponent
        if score > best_score or (score == best_score and (dx, dy) == (0, 0)):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]