def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    own = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    oxp = observation["opponent_position"][0]
    oyp = observation["opponent_position"][1]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    frontier = []
    for (x, y) in unclaimed:
        if (x, y) in obstacles:
            continue
        for dx, dy in dirs:
            nx, ny = x - dx, y - dy
            if (nx, ny) in own or (nx, ny) in opp:
                frontier.append((x, y))
                break
    targets = frontier if frontier else unclaimed
    if not targets:
        # fallback: expand away from opponent but avoid obstacles using local best move
        targets = [(x, y) for (x, y) in own] if own else [(sx, sy)]

    # Build a deterministic "value" for each possible move (avoid obstacles, prefer creating/stealing, avoid self-traps)
    best_move = [0, 0]
    best_val = -10**18
    visited_hint = set()
    for p in (observation.get("self_path") or []):
        visited_hint.add(tuple(p))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Base: prefer moving toward chosen targets; if entry flips (opponent cell), value it strongly
        in_opp = (nx, ny) in opp
        in_own = (nx, ny) in own
        # Steering objective: pick nearest target that we can reach locally (prefer those close to our territory boundary)
        # Compute minimal distance to any target, but with early cutoff.
        md = 10**9
        for (tx, ty) in targets:
            d = abs(tx - nx) + abs(ty - ny)
            if d < md:
                md = d
                if md == 0:
                    break

        # Risk/parking penalties: discourage moving back to recently visited cells unless it's opponent-owned
        back_pen = 8 if (nx, ny) in visited_hint else 0

        # Territorial pressure: prefer cells near opponent to contest, but keep some bias to expand
        opp_adj = 0
        for ax, ay in dirs:
            px, py = nx + ax, ny + ay
            if inb(px, py) and (px, py) in opp:
                opp_adj += 1

        # If opponent is far, edge-claim behavior by moving toward their region; else focus on nearest frontier
        toward_opp = abs(nx - oxp) + abs(ny - oyp)
        toward_score = -toward_opp

        val = 0
        val += (50 if in_opp else 0)
        val += (6 if in_own else 0)
        val += (-md) * 3
        val += opp_adj * 2
        val += toward_score * 0.2
        val -= back_pen

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    # If all moves invalid (surrounded), stay
    return best_move if best_move in ([-1, -1], [0, -1], [1, -1], [-1, 0], [0, 0], [1, 0], [-1, 1], [0, 1], [1, 1]) else [0, 0]